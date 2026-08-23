import { useEffect } from 'react'
import { useNavigate } from 'react-router-dom'

/**
 * Redirect to login if user is not authenticated or has wrong role.
 * @param {string} requiredRole - 'candidate' | 'company' | null (any authenticated)
 */
export function useAuth(requiredRole) {
  const navigate = useNavigate()

  useEffect(() => {
    const token = localStorage.getItem('recruitai.token')
    const role = localStorage.getItem('recruitai.role')
    const userId = localStorage.getItem('recruitai.user_id')

    if (!token || !userId) {
      navigate(requiredRole === 'company' ? '/login/company' : '/login/candidate')
      return
    }
    if (requiredRole && role !== requiredRole) {
      navigate('/')
    }
  }, [navigate, requiredRole])
}
