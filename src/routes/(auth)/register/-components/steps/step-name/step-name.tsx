import { useTranslate } from '@kanjou/react'

import { HeroButton, HeroInput, Typography } from '#/components/ui'

import { useStepName } from './hooks'

export function StepName() {
  const { features } = useStepName()

  const t = useTranslate()

  return (
    <form
      className="flex flex-1 flex-col"
      onSubmit={(event) => {
        event.preventDefault()
        void features.form.handleSubmit()
      }}
    >
      <Typography variant="title">{t('action.registration.title')}</Typography>
      <Typography variant="caption">{t('action.registration.description')}</Typography>
      <features.form.Field
        name="name"
        validators={{
          onSubmit: ({ value }) => (value.trim() === '' ? 'field.name.error.empty' : undefined),
        }}
      >
        {(field) => (
          <HeroInput
            name={field.name}
            value={field.state.value}
            onChange={(event) => field.handleChange(event.target.value)}
            onBlur={field.handleBlur}
            aria-invalid={field.state.meta.errors.length > 0}
            placeholder={t('field.name.placeholder')}
            className="mt-4"
            autoFocus
          />
        )}
      </features.form.Field>

      <div className="flex-1 flex flex-col justify-end">
        <HeroButton type="submit" className="w-full">
          {t('action.start.title')}
        </HeroButton>
        <Typography variant="caption" className="text-center mt-4">
          {t.rich('caption.has-account', { to: '/login' })}
        </Typography>
      </div>
    </form>
  )
}
