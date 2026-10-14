import { useMutation, useQueryClient } from '@tanstack/react-query'

import { createAward } from '../actions'
import { GROUP_QUERY_KEYS } from '../constants'

export function useCreateAwardMutation(groupId: string) {
  const queryClient = useQueryClient()

  return useMutation({
    mutationFn: createAward,
    onSuccess: async () => {
      await Promise.all([
        queryClient.invalidateQueries({ queryKey: GROUP_QUERY_KEYS.students(groupId) }),
        queryClient.invalidateQueries({ queryKey: GROUP_QUERY_KEYS.awards(groupId) }),
      ])
    },
  })
}
