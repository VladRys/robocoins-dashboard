import { useTranslate } from '@kanjou/react'

import { HeroButton, Typography } from '#/components/ui'

import { RegisterStep } from '../../register-provider'
import { MistakeCaption } from '../components/mistake-caption'
import { useStepView } from './hooks'

export function StepView() {
  const { state, mutations, functions } = useStepView()

  const t = useTranslate()

  return (
    <div className="flex flex-1 flex-col">
      <Typography variant="title">{t('step.view.title')}</Typography>
      <div className="flex items-center gap-3 mt-4">
        {state.avatarSrc && (
          <img src={state.avatarSrc} alt="" draggable={false} className="w-10 h-10" />
        )}
        <Typography variant="accent">{state.name}</Typography>
      </div>
      <Typography variant="subtitle" className="mt-2">
        {state.courseName}
      </Typography>
      <Typography variant="subtitle">
        {t('text.group')} {state.groupId}
      </Typography>

      <div className="flex-1 flex flex-col justify-end">
        <HeroButton onClick={functions.handleFinish} disabled={mutations.register.isPending}>
          {t('action.finish.title')}
        </HeroButton>
        <MistakeCaption to={RegisterStep.Avatar} />
      </div>
    </div>
  )
}
