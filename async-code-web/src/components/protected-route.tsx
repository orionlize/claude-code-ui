import { useAuth } from '@/contexts/auth-context'
import { useNavigate } from 'react-router-dom'
import { useEffect } from 'react'

interface ProtectedRouteProps {
    children: React.ReactNode
}

export function ProtectedRoute({ children }: ProtectedRouteProps) {
    const { user, loading } = useAuth()
    const navigate = useNavigate()

    useEffect(() => {
        if (!loading && !user) {
            navigate('/signin')
        }
    }, [user, loading, navigate])

    if (loading) {
        return (
            <div className="min-h-screen bg-gradient-to-br from-slate-50 to-slate-100 flex items-center justify-center">
                <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-slate-900"></div>
            </div>
        )
    }

    if (!user) {
        return null // Will redirect
    }

    return <>{children}</>
}