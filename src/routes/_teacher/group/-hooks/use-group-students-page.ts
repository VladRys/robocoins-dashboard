import { useNavigate, useParams } from '@tanstack/react-router'
import { useState } from 'react'

import { StudentSortOrder } from '../-constants'
import {
  AwardReason,
  useAwardsQuery,
  useCreateAwardMutation,
  useGroupQuery,
  useRevertAwardMutation,
  useStudentsQuery,
} from '../-mock'

export function useGroupStudentsPage() {
  const navigate = useNavigate()
  const params = useParams({ from: '/_teacher/group/$groupId' })

  const groupQuery = useGroupQuery(params.groupId)
  const studentsQuery = useStudentsQuery(params.groupId)
  const awardsQuery = useAwardsQuery(params.groupId)
  const createAwardMutation = useCreateAwardMutation(params.groupId)
  const revertAwardMutation = useRevertAwardMutation(params.groupId)

  const [searchQuery, setSearchQuery] = useState('')
  const [sortOrder, setSortOrder] = useState<StudentSortOrder>(StudentSortOrder.NameAsc)
  const [selectedStudentId, setSelectedStudentId] = useState<string | null>(null)
  const [isDrawerOpen, setIsDrawerOpen] = useState(false)

  function handleSearchChange(query: string) {
    setSearchQuery(query)
  }

  function handleSortChange(nextSortOrder: StudentSortOrder) {
    setSortOrder(nextSortOrder)
  }

  function handleSelectStudent(studentId: string) {
    setSelectedStudentId(studentId)
    setIsDrawerOpen(true)
  }

  function handleDrawerOpenChange(isOpen: boolean) {
    setIsDrawerOpen(isOpen)
  }

  function handleAward(studentId: string, amount: number, reason: AwardReason) {
    createAwardMutation.mutate({ studentId, amount, reason })
    setIsDrawerOpen(false)
  }

  function handleRevertAward(awardId: string) {
    revertAwardMutation.mutate(awardId)
  }

  function handleBackToGroups() {
    void navigate({ to: '/group' })
  }

  const students = studentsQuery.data || []
  const awards = awardsQuery.data || []

  const selectedStudent = students.find((student) => student.id === selectedStudentId) || null

  const studentAwards = awards.filter((award) => award.studentId === selectedStudentId)

  const filteredStudents = students.filter((student) => {
    return student.name.toLowerCase().includes(searchQuery.toLowerCase())
  })

  const sortedStudents = [...filteredStudents].sort((first, second) => {
    if (sortOrder === StudentSortOrder.NameAsc) return first.name.localeCompare(second.name)
    if (sortOrder === StudentSortOrder.NameDesc) return second.name.localeCompare(first.name)
    if (sortOrder === StudentSortOrder.BalanceDesc) return second.balance - first.balance
    if (sortOrder === StudentSortOrder.BalanceAsc) return first.balance - second.balance
    return 0
  })

  return {
    state: {
      group: groupQuery.data,
      students: sortedStudents,
      selectedStudent,
      studentAwards,
      searchQuery,
      sortOrder,
      isDrawerOpen,
    },
    queries: {
      group: groupQuery,
      students: studentsQuery,
      awards: awardsQuery,
    },
    mutations: {
      createAward: createAwardMutation,
      revertAward: revertAwardMutation,
    },
    functions: {
      handleSearchChange,
      handleSortChange,
      handleSelectStudent,
      handleDrawerOpenChange,
      handleAward,
      handleRevertAward,
      handleBackToGroups,
    },
  }
}
