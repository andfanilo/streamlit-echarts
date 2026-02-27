---
name: optimizing-streamlit-performance
description: Optimizing Streamlit app performance. Use when apps are slow, rerunning too often, or loading heavy content. Covers caching, fragments, and static vs dynamic widget choices.
license: Apache-2.0
---

# Streamlit performance

Performance is the biggest win. Without caching and fragments, your app reruns everything on every interaction.

## Caching

### @st.cache_data for data

Use for any function that loads or computes data.

```python
# BAD: Recomputes on every rerun
def load_data(path):
    return pd.read_csv(path)

# GOOD: Cached
@st.cache_data
def load_data(path):
    return pd.read_csv(path)
```

### @st.cache_resource for connections

Use for connections, API clients, ML models—objects that can't be serialized.

```python
@st.cache_resource
def get_connection():
    return st.connection("snowflake")

@st.cache_resource
def load_model():
    return torch.load("model.pt")
```

**Critical warning:** Never mutate `@st.cache_resource` returns—changes affect all users:

```python
# BAD: Mutating shared resource
@st.cache_resource
def get_config():
    return {"setting": "default"}

config = get_config()
config["setting"] = "custom"  # Affects ALL users!

# GOOD: Copy before modifying
config = get_config().copy()
config["setting"] = "custom"
```

**Cleanup with `on_release`:** Clean up resources when evicted from cache:

```python
def cleanup_connection(conn):
    conn.close()

@st.cache_resource(on_release=cleanup_connection)
def get_database():
    return create_connection()
```

### TTL for fresh data

```python
@st.cache_data(ttl="5m")  # 5 minutes
def get_metrics():
    return api.fetch()

@st.cache_data(ttl="1h")  # 1 hour
def load_reference_data():
    return pd.read_csv("large_reference.csv")
```

**Guidelines:**
- Real-time dashboards → `ttl="1m"` or less
- Metrics/reports → `ttl="5m"` to `ttl="15m"`
- Reference data → `ttl="1h"` or more
- Static data → No TTL

### Prevent unbounded cache growth

**Important:** Caches without `ttl` or `max_entries` can grow indefinitely and cause memory issues. For any cached function that stores changing objects (user-specific data, parameterized queries), set limits:

```python
# BAD: Unbounded cache - memory will grow indefinitely
@st.cache_data
def get_user_data(user_id):
    return fetch_user(user_id)

# GOOD: Bounded cache with TTL
@st.cache_data(ttl="1h")
def get_user_data(user_id):
    return fetch_user(user_id)

# GOOD: Bounded cache with max entries
@st.cache_data(max_entries=100)
def get_user_data(user_id):
    return fetch_user(user_id)
```

Use `ttl` for time-based expiration OR `max_entries` for size-based limits. You usually don't need both.

### Caching anti-patterns

**Don't cache functions that read widgets:**

```python
# BAD: Widget inside cached function
@st.cache_data
def filtered_data():
    query = st.text_input("Query")  # Widget inside cached function!
    return df[df["name"].str.contains(query)]

# GOOD: Pass widget values as parameters
@st.cache_data
def filtered_data(query: str):
    return df[df["name"].str.contains(query)]

query = st.text_input("Query")
result = filtered_data(query)
```

**Cache at the right granularity:**

```python
# BAD: Caching too much - new cache entry per filter value
@st.cache_data
def get_and_filter_data(filter_value):
    data = load_all_data()  # Expensive!
    return data[data["col"] == filter_value]

# GOOD: Cache the expensive part, filter separately
@st.cache_data(ttl="1h")
def load_all_data():
    return fetch_from_database()

data = load_all_data()
filtered = data[data["col"] == filter_value]
```

## Fragments

Use `@st.fragment` to isolate reruns for self-contained UI pieces.

```python
# BAD: Full app reruns
st.metric("Users", get_count())
if st.button("Refresh"):
    st.rerun()

# GOOD: Only fragment reruns
@st.fragment
def live_metrics():
    st.metric("Users", get_count())
    st.button("Refresh")

live_metrics()
```

For auto-refreshing metrics, use `run_every`:
```python
@st.fragment(run_every="30s")
def auto_refresh_metrics():
    st.metric("Users", get_count())

auto_refresh_metrics()
```

Use for: live metrics, refresh buttons, interactive charts that don't affect global state.

## Forms to batch interactions

By default, every widget interaction triggers a full rerun. Use `st.form` to batch multiple inputs and only rerun on submit.

```python
# BAD: Reruns on every keystroke and selection
name = st.text_input("Name")
email = st.text_input("Email")
role = st.selectbox("Role", ["Admin", "User"])

# GOOD: Single rerun when user clicks Submit
with st.form("user_form"):
    name = st.text_input("Name")
    email = st.text_input("Email")
    role = st.selectbox("Role", ["Admin", "User"])
    submitted = st.form_submit_button("Submit")

if submitted:
    save_user(name, email, role)
```

Use `border=False` for seamless inline forms that don't look like forms:

```python
with st.form("search", border=False):
    with st.container(horizontal=True):
        query = st.text_input("Search", label_visibility="collapsed")
        st.form_submit_button(":material/search:")
```

**When to use forms:**
- Multiple related inputs (signup, filters, settings)
- Text inputs where typing triggers expensive operations
- Any UI where "submit" semantics make sense

**When NOT to use forms:** If inputs depend on each other (e.g., selecting a country should update available cities), forms won't work since there's no rerun until submit.

## Conditional rendering

**This is critical and often missed.**

Layout containers like `st.tabs`, `st.expander`, and `st.popover` always render all their content, even when hidden or collapsed.

To render content only when needed, use elements like `st.segmented_control`, `st.toggle`, or `@st.dialog` with conditional logic:

```python
# BAD: Heavy content loads even when tab not visible
tab1, tab2 = st.tabs(["Light", "Heavy"])
with tab2:
    expensive_chart()  # Always computed!

# GOOD: Content only loads when selected
view = st.segmented_control("View", ["Light", "Heavy"])
if view == "Heavy":
    expensive_chart()  # Only computed when selected
```

```python
# BAD: Expander content always loads
with st.expander("Advanced options"):
    heavy_computation()  # Runs even when collapsed!

# GOOD: Toggle controls loading
if st.toggle("Show advanced options"):
    heavy_computation()  # Only runs when toggled on
```

## Pre-computation

Move expensive work outside the main flow:
- Compute aggregations in SQL/dbt, not Python
- Pre-compute metrics in scheduled jobs
- Use materialized views for complex queries

## Large data handling

### For datasets under ~100M rows

```python
@st.cache_data
def load_data():
    return pd.read_parquet("large_file.parquet")
```

### For very large datasets (over ~100M rows)

> **Note:** This is only an escape hatch when serialization becomes too slow. In most cases, data this large shouldn't be loaded entirely into memory—prefer using a database that queries and loads data on demand.

`@st.cache_data` uses pickle which slows with huge data. Use `@st.cache_resource` instead:

```python
@st.cache_resource  # No serialization overhead
def load_huge_data():
    return pd.read_parquet("huge_file.parquet")

# WARNING: Don't mutate the returned DataFrame!
```

### Sampling for exploration

When exploring large datasets, load a random sample instead of the full data:

```python
@st.cache_data(ttl="1h")
def load_sample(n=10000):
    df = pd.read_parquet("huge.parquet")
    return df.sample(n=n)
```

## Multithreading

Custom threads cannot call Streamlit commands (no session context).

```python
import threading

def fetch_in_background(url, results, index):
    results[index] = requests.get(url).json()  # No st.* calls!

# Collect results, then display in main thread
results = [None] * len(urls)
threads = [
    threading.Thread(target=fetch_in_background, args=(url, results, i))
    for i, url in enumerate(urls)
]
for t in threads:
    t.start()
for t in threads:
    t.join()

# Now display in main thread
for result in results:
    st.write(result)
```

**Prefer alternatives when possible:**
- `@st.cache_data` for expensive computations
- `@st.fragment(run_every="5s")` for periodic updates

## References

- [Caching overview](https://docs.streamlit.io/develop/concepts/architecture/caching)
- [st.cache_data](https://docs.streamlit.io/develop/api-reference/caching-and-state/st.cache_data)
- [st.cache_resource](https://docs.streamlit.io/develop/api-reference/caching-and-state/st.cache_resource)
- [st.fragment](https://docs.streamlit.io/develop/api-reference/execution-flow/st.fragment)
- [st.form](https://docs.streamlit.io/develop/api-reference/execution-flow/st.form)