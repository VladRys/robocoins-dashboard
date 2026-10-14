import { useQuery } from '@tanstack/react-query'

import { fetchAwards } from '../actions'
import { GROUP_QUERY_KEYS } from '../constants'

export function useAwardsQuery(groupId: string) {
  return useQuery({
    queryKey: GROUP_QUERY_KEYS.awards(groupId),
    queryFn: () => fetchAwards(groupId),
  })
}
