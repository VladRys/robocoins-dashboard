import { useNavigate } from "@tanstack/react-router";

import { useCreateStudentStudentRegisterPost } from "#/api/hooks";
import { LOCALSTORAGE_DID_REGISTER } from "#/routes/-constants";

import { AVATARS } from "../../../../-constants";
import { registerDraft } from "../../../../-lib";
import { useRegisterContext } from "../../../register-provider";

export function useStepView() {
  const register = useRegisterContext();

  const navigate = useNavigate();

  const registerMutation = useCreateStudentStudentRegisterPost({
    mutation: {
      onSuccess: () => {
        registerDraft.clear();
        localStorage.setItem(LOCALSTORAGE_DID_REGISTER, "true");
        void navigate({ to: "/" });
      },
    },
  });

  const avatar = register.state.avatar as keyof typeof AVATARS | undefined;

  const handleFinish = () => {
    const { name, avatar, courseName, groupId } = register.state;

    if (!name || !avatar || !courseName || groupId === undefined) return;

    registerMutation.mutate({
      body: { name, avatar, course_name: courseName, group_id: groupId },
    });
  };

  return {
    state: {
      name: register.state.name,
      avatarSrc: avatar ? AVATARS[avatar] : undefined,
      courseName: register.state.courseName,
      groupId: register.state.groupId,
    },
    queries: {},
    mutations: {
      register: registerMutation,
    },
    functions: {
      handleFinish,
    },
    features: {},
  };
}
