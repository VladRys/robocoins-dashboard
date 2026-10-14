import { useQuery } from '@tanstack/react-query'

import { fetchGroups } from '../actions'
import { GROUP_QUERY_KEYS } from '../constants'

export function useGroupsQuery() {
  return useQuery({
    queryKey: GROUP_QUERY_KEYS.groups,
    queryFn: fetchGroups,
  })
}
