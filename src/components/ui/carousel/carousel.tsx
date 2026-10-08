import { cn } from 'cn'
import useEmblaCarousel, { type UseEmblaCarouselType } from 'embla-carousel-react'
import {
  ComponentProps,
  createContext,
  KeyboardEvent,
  use,
  useCallback,
  useEffect,
  useState,
} from 'react'

import styles from './carousel.module.css'

export type CarouselApi = UseEmblaCarouselType[1]
type UseCarouselParameters = Parameters<typeof useEmblaCarousel>
export type CarouselOptions = UseCarouselParameters[0]
export type CarouselPlugin = UseCarouselParameters[1]

export interface CarouselProps extends ComponentProps<'div'> {
  opts?: CarouselOptions
  plugins?: CarouselPlugin
  setApi?: (api: CarouselApi) => void
}

interface CarouselContextValue {
  carouselRef: UseEmblaCarouselType[0]
  api: CarouselApi
  selectedIndex: number
  scrollPrev: () => void
  scrollNext: () => void
  scrollTo: (index: number) => void
}

const CarouselContext = createContext<CarouselContextValue | null>(null)

export function useCarousel() {
  const context = use(CarouselContext)

  if (!context) throw new Error('useCarousel must be used within a <Carousel />')

  return context
}

export function Carousel({ opts, plugins, setApi, className, children, ...props }: CarouselProps) {
  const [carouselRef, api] = useEmblaCarousel({ ...opts, axis: 'x' }, plugins)
  const [selectedIndex, setSelectedIndex] = useState(opts?.startIndex ?? 0)

  const scrollPrev = useCallback(() => api?.scrollPrev(), [api])
  const scrollNext = useCallback(() => api?.scrollNext(), [api])
  const scrollTo = useCallback((index: number) => api?.scrollTo(index), [api])

  const handleKeyDown = (event: KeyboardEvent<HTMLDivElement>) => {
    if (event.key === 'ArrowLeft') {
      event.preventDefault()
      scrollPrev()
    } else if (event.key === 'ArrowRight') {
      event.preventDefault()
      scrollNext()
    }
  }

  useEffect(() => {
    if (!api || !setApi) return
    setApi(api)
  }, [api, setApi])

  useEffect(() => {
    if (!api) return

    const onSelect = (api: NonNullable<CarouselApi>) => setSelectedIndex(api.selectedScrollSnap())

    onSelect(api)
    api.on('reInit', onSelect)
    api.on('select', onSelect)

    return () => {
      api.off('reInit', onSelect)
      api.off('select', onSelect)
    }
  }, [api])

  return (
    <CarouselContext value={{ carouselRef, api, selectedIndex, scrollPrev, scrollNext, scrollTo }}>
      <div
        {...props}
        onKeyDownCapture={handleKeyDown}
        className={cn(styles.carousel, className)}
        role="region"
        aria-roledescription="carousel"
      >
        {children}
      </div>
    </CarouselContext>
  )
}

export interface CarouselContentProps extends ComponentProps<'div'> {}

export function CarouselContent({ className, ...props }: CarouselContentProps) {
  const { carouselRef } = useCarousel()

  return (
    <div ref={carouselRef} className={styles.viewport}>
      <div {...props} className={cn(styles.container, className)} />
    </div>
  )
}

export interface CarouselItemProps extends ComponentProps<'div'> {}

export function CarouselItem({ className, ...props }: CarouselItemProps) {
  return (
    <div
      {...props}
      role="group"
      aria-roledescription="slide"
      className={cn(styles.item, className)}
    />
  )
}
