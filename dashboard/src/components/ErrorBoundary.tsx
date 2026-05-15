import { Component, ReactNode } from 'react'

interface Props {
  children: ReactNode
  fallback?: ReactNode
}

interface State {
  hasError: boolean
  error?: Error
}

export default class ErrorBoundary extends Component<Props, State> {
  state: State = { hasError: false }

  static getDerivedStateFromError(error: Error): State {
    return { hasError: true, error }
  }

  componentDidCatch(error: Error, info: React.ErrorInfo) {
    console.error('[ErrorBoundary]', error, info)
  }

  render() {
    if (this.state.hasError) {
      return (
        this.props.fallback || (
          <div className="vnx-card text-center p-8">
            <h3 className="text-lg font-semibold text-vnx-red mb-2">Something went wrong</h3>
            <p className="text-sm text-gray-400">{this.state.error?.message}</p>
            <button
              className="mt-4 px-4 py-2 bg-blue-600 rounded text-white text-sm hover:bg-blue-700"
              onClick={() => this.setState({ hasError: false })}
            >
              Retry
            </button>
          </div>
        )
      )
    }
    return this.props.children
  }
}
