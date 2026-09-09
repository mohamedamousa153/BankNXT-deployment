with open("frontend/app.jsx", "r") as f:
    content = f.read()

old_func = """function formatDateOnly(dateString) {
    if(!dateString) return "";
    const d = new Date(dateString);
    return d.toISOString().split('T')[0];
}"""

new_func = """function formatDateOnly(dateString) {
    if(!dateString) return "";
    try {
        const d = new Date(dateString);
        if (isNaN(d.getTime())) return String(dateString);
        return d.toISOString().split('T')[0];
    } catch(e) {
        return String(dateString);
    }
}"""

content = content.replace(old_func, new_func)

old_datetime_func = """function formatDateTime(isoString) {
    if(!isoString) return "";
    const d = new Date(isoString);
    return `${d.toLocaleDateString()} ${d.toLocaleTimeString([], {hour: '2-digit', minute:'2-digit'})}`;
}"""

new_datetime_func = """function formatDateTime(isoString) {
    if(!isoString) return "";
    try {
        const d = new Date(isoString);
        if (isNaN(d.getTime())) return String(isoString);
        return `${d.toLocaleDateString()} ${d.toLocaleTimeString([], {hour: '2-digit', minute:'2-digit'})}`;
    } catch(e) {
        return String(isoString);
    }
}"""

content = content.replace(old_datetime_func, new_datetime_func)

with open("frontend/app.jsx", "w") as f:
    f.write(content)
