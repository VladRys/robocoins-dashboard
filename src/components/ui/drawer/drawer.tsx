import { Drawer as DrawerPrimitive } from '@base-ui/react/drawer'
import { cn } from 'cn'
import { ComponentProps, createContext, useContext, useMemo } from 'react'

import styles from './drawer.module.css'

interface DrawerContextValue {
  modal: DrawerPrimitive.Root.Props['modal']
  showSwipeHandle: boolean
}

const DrawerContext = createContext<DrawerContextValue | null>(null)

function useDrawerContext() {
  const context = useContext(DrawerContext)

  if (!context) {
    throw new Error('useDrawerContext must be used within a Drawer.')
  }

  return context
}

export interface DrawerProps extends DrawerPrimitive.Root.Props {
  showSwipeHandle?: boolean
}

export function Drawer({
  modal = true,
  showSwipeHandle = false,
  swipeDirection = 'down',
  ...props
}: DrawerProps) {
  const contextValue = useMemo(() => ({ modal, showSwipeHandle }), [modal, showSwipeHandle])

  return (
    <DrawerContext.Provider value={contextValue}>
      <DrawerPrimitive.Root modal={modal} swipeDirection={swipeDirection} {...props} />
    </DrawerContext.Provider>
  )
}

export interface DrawerTriggerProps extends DrawerPrimitive.Trigger.Props {}

export function DrawerTrigger(props: DrawerTriggerProps) {
  return <DrawerPrimitive.Trigger {...props} />
}

export interface DrawerCloseProps extends DrawerPrimitive.Close.Props {}

export function DrawerClose(props: DrawerCloseProps) {
  return <DrawerPrimitive.Close {...props} />
}

export interface DrawerPortalProps extends DrawerPrimitive.Portal.Props {}

export function DrawerPortal(props: DrawerPortalProps) {
  return <DrawerPrimitive.Portal {...props} />
}

export interface DrawerOverlayProps extends DrawerPrimitive.Backdrop.Props {}

export function DrawerOverlay({ className, ...props }: DrawerOverlayProps) {
  return <DrawerPrimitive.Backdrop {...props} className={cn(styles.overlay, className)} />
}

export interface DrawerSwipeHandleProps extends ComponentProps<'div'> {}

export function DrawerSwipeHandle({ className, ...props }: DrawerSwipeHandleProps) {
  return <div aria-hidden="true" {...props} className={cn(styles['swipe-handle'], className)} />
}

export interface DrawerContentProps extends DrawerPrimitive.Popup.Props {}

export function DrawerContent({ className, children, ...props }: DrawerContentProps) {
  const context = useDrawerContext()
  const isModal = context.modal === true

  return (
    <DrawerPortal>
      {isModal && <DrawerOverlay />}
      <DrawerPrimitive.Viewport data-modal={context.modal} className={styles.viewport}>
        <DrawerPrimitive.Popup {...props} className={cn(styles.popup, className)}>
          {context.showSwipeHandle && <DrawerSwipeHandle />}
          <DrawerPrimitive.Content className={styles.content}>{children}</DrawerPrimitive.Content>
        </DrawerPrimitive.Popup>
      </DrawerPrimitive.Viewport>
    </DrawerPortal>
  )
}

export interface DrawerHeaderProps extends ComponentProps<'div'> {}

export function DrawerHeader({ className, ...props }: DrawerHeaderProps) {
  return <div {...props} className={cn(styles.header, className)} />
}

export interface DrawerFooterProps extends ComponentProps<'div'> {}

export function DrawerFooter({ className, ...props }: DrawerFooterProps) {
  return <div {...props} className={cn(styles.footer, className)} />
}

export interface DrawerTitleProps extends DrawerPrimitive.Title.Props {}

export function DrawerTitle({ className, ...props }: DrawerTitleProps) {
  return <DrawerPrimitive.Title {...props} className={cn(styles.title, className)} />
}

export interface DrawerDescriptionProps extends DrawerPrimitive.Description.Props {}

export function DrawerDescription({ className, ...props }: DrawerDescriptionProps) {
  return <DrawerPrimitive.Description {...props} className={cn(styles.description, className)} />
}
