import { createFileRoute, Outlet, redirect } from "@tanstack/react-router"

import { AppBottomNav } from "@/components/Common/AppBottomNav"
import { TopBar } from "@/components/Common/TopBar"
import { isLoggedIn } from "@/hooks/useAuth"

export const Route = createFileRoute("/_layout")({
  component: Layout,
  beforeLoad: async () => {
    if (!isLoggedIn()) {
      throw redirect({
        to: "/login",
      })
    }
  },
})

function Layout() {
  return (
    <div className="flex min-h-dvh flex-col bg-background">
      <TopBar />
      <main className="flex-1 px-4 pb-28 pt-6">
        <div className="mx-auto w-full max-w-3xl">
          <Outlet />
        </div>
      </main>
      <div className="fixed inset-x-0 bottom-0 z-10 px-4 pb-[max(0.75rem,env(safe-area-inset-bottom))] pt-2">
        <div className="mx-auto w-full max-w-3xl">
          <AppBottomNav />
        </div>
      </div>
    </div>
  )
}

export default Layout
