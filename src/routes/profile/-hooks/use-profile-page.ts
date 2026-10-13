import { useRouteContext } from '@tanstack/react-router'

const MOCK_PROFILE = {
  name: 'Данило',
  avatar: '/star-struck.png',
  balance: 2480,
}

export function useProfilePage() {
  const { user } = useRouteContext({ from: '__root__' })

  return {
    state: user ?? MOCK_PROFILE,
  }
}
