import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query"
import { useNavigate } from "@tanstack/react-router"

import { AuthService, type UtenteLogin, type UtentePublic } from "@/lib/api"
import { handleError } from "@/utils"
import useCustomToast from "./useCustomToast"

const isLoggedIn = () => {
  return localStorage.getItem("access_token") !== null
}

const useAuth = () => {
  const navigate = useNavigate()
  const queryClient = useQueryClient()
  const { showErrorToast } = useCustomToast()

  const { data: user } = useQuery<UtentePublic | null, Error>({
    queryKey: ["currentUser"],
    queryFn: AuthService.readMe,
    enabled: isLoggedIn(),
  })

  const login = async (data: UtenteLogin) => {
    const response = await AuthService.login({ requestBody: data })
    localStorage.setItem("access_token", response.access_token)
  }

  const loginMutation = useMutation({
    mutationFn: login,
    onSuccess: () => {
      navigate({ to: "/" })
    },
    onError: handleError.bind(showErrorToast),
  })

  const logout = async () => {
    // Revoke the session server-side (FR-2); clear locally regardless of the
    // network result so the device is always signed out.
    try {
      await AuthService.logout()
    } catch {
      // best-effort revocation
    }
    localStorage.removeItem("access_token")
    queryClient.removeQueries({ queryKey: ["currentUser"] })
    navigate({ to: "/login" })
  }

  return {
    loginMutation,
    logout,
    user,
  }
}

export { isLoggedIn }
export default useAuth
