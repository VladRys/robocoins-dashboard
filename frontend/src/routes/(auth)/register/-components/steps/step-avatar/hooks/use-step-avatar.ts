import { useForm } from "@tanstack/react-form";
import { useEffect, useState } from "react";

import type { CarouselApi } from "#/components/ui";

import { AVATAR_KEYS, AvatarKey } from "../../../../-constants";
import { RegisterStep, useRegisterContext } from "../../../register-provider";

export function useStepAvatar() {
  const register = useRegisterContext();

  const savedIndex = AVATAR_KEYS.findIndex((key) => key === register.state.avatar);
  const initialIndex = savedIndex === -1 ? Math.floor(AVATAR_KEYS.length / 2) : savedIndex;

  const form = useForm({
    defaultValues: { avatar: AVATAR_KEYS[initialIndex] as AvatarKey },
    onSubmit: ({ value }) => {
      register.goTo(RegisterStep.View, { avatar: value.avatar });
    },
  });

  const [api, setApi] = useState<CarouselApi>();

  useEffect(() => {
    if (!api) return;

    const onSelect = () => form.setFieldValue("avatar", AVATAR_KEYS[api.selectedScrollSnap()]);

    api.on("select", onSelect);

    return () => {
      api.off("select", onSelect);
    };
  }, [api, form]);

  return {
    state: {
      initialIndex,
    },
    queries: {},
    mutations: {},
    functions: {
      setApi,
    },
    features: {
      form,
    },
  };
}
