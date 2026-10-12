import { useTranslate } from '@kanjou/react'
import { createFileRoute } from '@tanstack/react-router'

import { HeroButton, Typography } from '#/components/ui'

import { HeroPasswordInput } from './-components'
import { useLoginPage } from './-hooks'

export const Route = createFileRoute('/(auth)/login/')({
  component: RouteComponent,
})

function RouteComponent() {
  const { functions, features } = useLoginPage()

  const t = useTranslate()

  return (
    <form className="flex flex-1 flex-col" onSubmit={functions.handleSubmit}>
      <Typography variant="title">{t('action.login.title')}</Typography>
      <features.form.Field name="password">
        {(field) => (
          <HeroPasswordInput
            name={field.name}
            value={field.state.value}
            onChange={(event) => field.handleChange(event.target.value)}
            onBlur={field.handleBlur}
            aria-invalid={!!field.state.meta.errors.length}
            className="mt-4"
            autoFocus
          />
        )}
      </features.form.Field>

      <div className="flex-1 flex flex-col justify-end">
        <HeroButton type="submit" className="w-full">
          {t('action.enter.title')}
        </HeroButton>
        <Typography variant="caption" className="text-center mt-4">
          {t.rich('caption.has-no-account', { to: '/register' })}
        </Typography>
      </div>
    </form>
  )
}
