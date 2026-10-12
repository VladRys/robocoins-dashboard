import { createFileRoute, Outlet } from '@tanstack/react-router'
import { cn } from 'cn'

import { RegisterProvider } from './-components/register-provider'
import { LOCALSTORAGE_REGISTER_STATE } from './-constants'
import { DEFAULT_REGISTER_STATE, JsonSchema, RegisterStateSchema } from './-schemas'

import styles from './route.module.css'

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
    <div className={styles.wrapper}>
      <div className={cn('i-ph:coins', styles.coins)} />
      <RegisterProvider initialState={initialState}>
        <Outlet />
      </RegisterProvider>
    </div>
  )
}
