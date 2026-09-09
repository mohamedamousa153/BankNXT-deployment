with open("frontend/app.jsx", "r") as f:
    content = f.read()

error_boundary = """
class ErrorBoundary extends React.Component {
  constructor(props) {
    super(props);
    this.state = { hasError: false, error: null, errorInfo: null };
  }
  componentDidCatch(error, errorInfo) {
    this.setState({ hasError: true, error: error, errorInfo: errorInfo });
    console.error("ErrorBoundary caught an error", error, errorInfo);
  }
  render() {
    if (this.state.hasError) {
      return (
        <div style={{ padding: '20px', background: '#fee', color: '#900', border: '1px solid #c00', margin: '20px', borderRadius: '8px', fontFamily: 'monospace' }}>
          <h2>Something went wrong.</h2>
          <p><b>{this.state.error && this.state.error.toString()}</b></p>
          <pre style={{ whiteSpace: 'pre-wrap', fontSize: '12px' }}>
            {this.state.errorInfo && this.state.errorInfo.componentStack}
          </pre>
        </div>
      );
    }
    return this.props.children;
  }
}
"""

if "class ErrorBoundary" not in content:
    content = error_boundary + content

content = content.replace("<App />", "<ErrorBoundary><App /></ErrorBoundary>")

with open("frontend/app.jsx", "w") as f:
    f.write(content)
