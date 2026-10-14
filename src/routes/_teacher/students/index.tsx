import { createFileRoute } from '@tanstack/react-router'

export const Route = createFileRoute('/_teacher/students/')({
  component: RouteComponent,
})

function RouteComponent() {
  return <div>Hello "/(teacher)/dashboard/"!</div>
}
