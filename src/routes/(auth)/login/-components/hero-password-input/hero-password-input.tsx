import { useTranslate } from '@kanjou/react'
import { cn } from 'cn'
import { useState } from 'react'

import {
  HeroInputGroup,
  HeroInputGroupButton,
  HeroInputGroupInput,
  type HeroInputGroupInputProps,
} from '#/components/ui'

export interface HeroPasswordInputProps extends Omit<HeroInputGroupInputProps, 'className'> {
  className?: string
}

export function HeroPasswordInput({ className, ...props }: HeroPasswordInputProps) {
  const [isRevealed, setIsRevealed] = useState(false)

  const t = useTranslate()

  const handleToggleRevealed = () => {
    setIsRevealed(!isRevealed)
  }

  const label = isRevealed ? t('field.password.hide') : t('field.password.show')
  const type = isRevealed ? 'text' : 'password'

  return (
    <HeroInputGroup className={className}>
      <HeroInputGroupInput {...props} placeholder="Твій пароль" type={type} />
      <HeroInputGroupButton
        onClick={handleToggleRevealed}
        aria-pressed={isRevealed}
        aria-label={label}
      >
        <div className={cn('i-ph:eye-bold', isRevealed && 'hidden')} />
        <div className={cn('i-ph:eye-slash-bold', !isRevealed && 'hidden')} />
      </HeroInputGroupButton>
    </HeroInputGroup>
  )
}
