import { useNavigate } from '@tanstack/react-router'
import { useState } from 'react'

import { GroupFilter } from '../-constants'
import { useGroupsQuery } from '../-mock'

export function useGroupPage() {
  const navigate = useNavigate()
  const groupsQuery = useGroupsQuery()
  const [selectedTheme, setSelectedTheme] = useState<GroupFilter>(GroupFilter.All)

  function handleThemeSelect(theme: GroupFilter) {
    setSelectedTheme(theme)
  }

  function handleGroupClick(groupId: string) {
    void navigate({ to: '/group/$groupId', params: { groupId } })
  }

  const groups = groupsQuery.data || []

  const filteredGroups = groups.filter((group) => {
    if (selectedTheme === GroupFilter.All) return true
    return group.theme === selectedTheme
  })

  return {
    state: {
      groups: filteredGroups,
      selectedTheme,
      allGroupsCount: groups.length,
    },
    queries: {
      groups: groupsQuery,
    },
    functions: {
      handleThemeSelect,
      handleGroupClick,
    },
  }
}
