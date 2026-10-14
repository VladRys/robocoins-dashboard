import { INITIAL_AWARDS, MOCK_GROUPS, MOCK_STUDENTS } from '../constants'
import { CreateAwardPayload, Group, Student, StudentAward } from '../types'

const LATENCY_IN_MILLISECONDS = 120

const database = {
  students: MOCK_STUDENTS.map((student) => ({ ...student })),
  awards: INITIAL_AWARDS.map((award) => ({ ...award })),
}

function wait() {
  return new Promise<void>((resolve) => {
    setTimeout(resolve, LATENCY_IN_MILLISECONDS)
  })
}

export async function fetchGroups(): Promise<Group[]> {
  await wait()
  return MOCK_GROUPS.map((group) => ({ ...group }))
}

export async function fetchGroup(groupId: string): Promise<Group> {
  await wait()
  const group = MOCK_GROUPS.find((item) => item.id === groupId)

  if (!group) {
    throw new Error('Group not found')
  }

  return { ...group }
}

export async function fetchStudents(groupId: string): Promise<Student[]> {
  await wait()
  return database.students
    .filter((student) => student.groupId === groupId)
    .map((student) => ({ ...student }))
}

export async function fetchAwards(groupId: string): Promise<StudentAward[]> {
  await wait()
  const studentIds = database.students
    .filter((student) => student.groupId === groupId)
    .map((student) => student.id)

  return database.awards
    .filter((award) => studentIds.includes(award.studentId))
    .map((award) => ({ ...award }))
}

function changeBalance(studentId: string, amount: number) {
  database.students = database.students.map((student) => {
    if (student.id === studentId) {
      return { ...student, balance: Math.max(0, student.balance + amount) }
    }
    return student
  })
}

export async function createAward(payload: CreateAwardPayload): Promise<StudentAward> {
  await wait()
  const award: StudentAward = {
    id: `award-${Date.now()}`,
    studentId: payload.studentId,
    amount: payload.amount,
    reason: payload.reason,
    timestamp: 'Щойно',
  }

  database.awards = [award, ...database.awards]
  changeBalance(payload.studentId, payload.amount)

  return { ...award }
}

export async function revertAward(awardId: string): Promise<void> {
  await wait()
  const award = database.awards.find((item) => item.id === awardId)

  if (!award) {
    throw new Error('Award not found')
  }

  database.awards = database.awards.filter((item) => item.id !== awardId)
  changeBalance(award.studentId, -award.amount)
}
