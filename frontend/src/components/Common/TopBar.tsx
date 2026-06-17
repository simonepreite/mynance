import { Link as RouterLink } from "@tanstack/react-router"
import { LogOut, Settings, Tags } from "lucide-react"

import { Appearance } from "@/components/Common/Appearance"
import { Logo } from "@/components/Common/Logo"
import { Avatar, AvatarFallback } from "@/components/ui/avatar"
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuLabel,
  DropdownMenuSeparator,
  DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu"
import useAuth from "@/hooks/useAuth"
import { getInitials } from "@/utils"

export function TopBar() {
  const { user, logout } = useAuth()

  return (
    <header className="sticky top-0 z-10 flex h-16 items-center justify-between gap-2 border-b bg-background px-4">
      <RouterLink to="/" aria-label="Home" className="flex items-center">
        <Logo variant="responsive" />
      </RouterLink>

      <div className="flex items-center gap-2">
        <Appearance />
        <DropdownMenu>
          <DropdownMenuTrigger
            className="rounded-full outline-none focus-visible:ring-2 focus-visible:ring-ring"
            aria-label="Menu account"
            data-testid="account-menu"
          >
            <Avatar className="size-8">
              <AvatarFallback className="bg-zinc-600 text-white">
                {getInitials(user?.username || "Utente")}
              </AvatarFallback>
            </Avatar>
          </DropdownMenuTrigger>
          <DropdownMenuContent align="end" className="min-w-48">
            <DropdownMenuLabel className="truncate">
              {user?.username ?? "Account"}
            </DropdownMenuLabel>
            <DropdownMenuSeparator />
            <RouterLink to="/categorie">
              <DropdownMenuItem>
                <Tags />
                Categorie
              </DropdownMenuItem>
            </RouterLink>
            <RouterLink to="/settings">
              <DropdownMenuItem>
                <Settings />
                Impostazioni
              </DropdownMenuItem>
            </RouterLink>
            <DropdownMenuSeparator />
            <DropdownMenuItem onClick={() => logout()} data-testid="logout">
              <LogOut />
              Esci
            </DropdownMenuItem>
          </DropdownMenuContent>
        </DropdownMenu>
      </div>
    </header>
  )
}
