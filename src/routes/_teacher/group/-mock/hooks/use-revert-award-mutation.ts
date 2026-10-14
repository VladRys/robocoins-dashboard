import { useMutation, useQueryClient } from '@tanstack/react-query'

import { revertAward } from '../actions'
import { GROUP_QUERY_KEYS } from '../constants'

export function useRevertAwardMutation(groupId: string) {
  const queryClient = useQueryClient()

  return useMutation({
    mutationFn: revertAward,
    onSuccess: async () => {
      await Promise.all([
        queryClient.invalidateQueries({ queryKey: GROUP_QUERY_KEYS.students(groupId) }),
        queryClient.invalidateQueries({ queryKey: GROUP_QUERY_KEYS.awards(groupId) }),
      ])
    },
  })
}
