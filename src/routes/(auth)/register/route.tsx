import { createFileRoute, Outlet } from '@tanstack/react-router'

import { RegisterProvider } from './-components/register-provider'
import { LOCALSTORAGE_REGISTER_STATE } from './-constants'
import { DEFAULT_REGISTER_STATE, JsonSchema, RegisterStateSchema } from './-schemas'

export const Route = createFileRoute('/(auth)/register')({
  component: RouteComponent,
  loader: () => {
    const draft = localStorage.getItem(LOCALSTORAGE_REGISTER_STATE)

    if (draft) {
      const parsed = JsonSchema.pipe(RegisterStateSchema).safeParse(draft)

      if (parsed.success) return parsed.data

      localStorage.removeItem(LOCALSTORAGE_REGISTER_STATE)
    }

    return DEFAULT_REGISTER_STATE
  },
})

function RouteComponent() {
  const initialState = Route.useLoaderData()

  return (
    <RegisterProvider initialState={initialState}>
      <Outlet />
    </RegisterProvider>
  )
}
