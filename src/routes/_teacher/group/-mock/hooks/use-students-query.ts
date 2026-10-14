import { useQuery } from '@tanstack/react-query'

import { fetchStudents } from '../actions'
import { GROUP_QUERY_KEYS } from '../constants'

export function useStudentsQuery(groupId: string) {
  return useQuery({
    queryKey: GROUP_QUERY_KEYS.students(groupId),
    queryFn: () => fetchStudents(groupId),
  })
}
