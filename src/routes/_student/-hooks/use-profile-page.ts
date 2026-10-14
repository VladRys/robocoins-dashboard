import { useRouteContext } from '@tanstack/react-router'

import { Avatar } from '#/routes/_auth/register/-constants'

const MOCK_PROFILE: { name: string; avatar: Avatar; balance: number } = {
  name: 'Данило',
  avatar: 'star-struck',
  balance: 2480,
} as const

export function useProfilePage() {
  const { user } = useRouteContext({ from: '__root__' })

  return {
    state: user ?? MOCK_PROFILE,
  }
}
