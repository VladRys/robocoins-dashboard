import { useQuery } from '@tanstack/react-query'

import { fetchGroup } from '../actions'
import { GROUP_QUERY_KEYS } from '../constants'

export function useGroupQuery(groupId: string) {
  return useQuery({
    queryKey: GROUP_QUERY_KEYS.group(groupId),
    queryFn: () => fetchGroup(groupId),
  })
}
