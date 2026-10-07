import { cn } from "cn";
import { Children, ComponentProps, createContext, use } from "react";

import { Carousel, CarouselContent, CarouselItem, CarouselProps, useCarousel } from "../carousel";

import styles from "./hero-carousel.module.css";

export function HeroCarousel({ className, opts, ...props }: CarouselProps) {
  return (
    <Carousel
      {...props}
      opts={{ align: "center", containScroll: false, ...opts }}
      className={cn(styles.hero, className)}
    />
  );
}

const HeroCarouselItemIndexContext = createContext(0);

export interface HeroCarouselContentProps extends ComponentProps<"div"> {}

export function HeroCarouselContent({ className, children, ...props }: HeroCarouselContentProps) {
  return (
    <CarouselContent {...props} className={cn(styles.content, className)}>
      {Children.map(children, (child, index) => (
        <HeroCarouselItemIndexContext value={index}>{child}</HeroCarouselItemIndexContext>
      ))}
    </CarouselContent>
  );
}

export interface HeroCarouselItemProps extends ComponentProps<"div"> {}

export function HeroCarouselItem({ className, children, ...props }: HeroCarouselItemProps) {
  const { selectedIndex, scrollTo } = useCarousel();
  const index = use(HeroCarouselItemIndexContext);

  const isActive = index === selectedIndex;

  return (
    <CarouselItem {...props} className={cn(styles.item, className)}>
      <div
        className={styles.card}
        data-active={isActive || undefined}
        onClick={() => scrollTo(index)}
      >
        {children}
      </div>
    </CarouselItem>
  );
}
