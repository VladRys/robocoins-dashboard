import { useTranslate } from '@kanjou/react'

import {
  HeroButton,
  HeroCarousel,
  HeroCarouselContent,
  HeroCarouselItem,
  Typography,
} from '#/components/ui'

import { AVATARS, AVATAR_KEYS } from '../../../-constants'
import { RegisterStep } from '../../register-provider'
import { MistakeCaption } from '../components/mistake-caption'
import { useStepAvatar } from './hooks'

export function StepAvatar() {
  const { state, functions, features } = useStepAvatar()

  const t = useTranslate()

  return (
    <form
      className="flex flex-1 flex-col"
      onSubmit={(event) => {
        event.preventDefault()
        void features.form.handleSubmit()
      }}
    >
      <Typography variant="title">{t('step.avatar.title')}</Typography>
      <HeroCarousel
        className="mt-8"
        opts={{ startIndex: state.initialIndex }}
        setApi={functions.setApi}
      >
        <HeroCarouselContent>
          {AVATAR_KEYS.map((key) => (
            <HeroCarouselItem key={key}>
              <img
                src={AVATARS[key]}
                alt={key}
                draggable={false}
                className="w-full h-full select-none pointer-events-none"
              />
            </HeroCarouselItem>
          ))}
        </HeroCarouselContent>
      </HeroCarousel>

      <div className="flex-1 flex flex-col justify-end">
        <HeroButton type="submit">{t('action.next.title')}</HeroButton>
        <MistakeCaption to={RegisterStep.Group} />
      </div>
    </form>
  )
}
