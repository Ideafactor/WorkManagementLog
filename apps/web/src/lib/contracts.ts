import { z } from "zod";

export const userSchema = z.object({
  id: z.number().int().positive(),
  email: z.string().email(),
  name: z.string(),
  role: z.enum(["MEMBER", "ADMIN"]),
  status: z.enum(["ACTIVE", "DISABLED"]),
  mustChangePassword: z.boolean(),
  version: z.number().int().positive(),
});

export const sessionSchema = z.object({
  user: userSchema,
  expiresAt: z.string().datetime({ offset: true }),
  csrfToken: z.string().nullable().optional(),
});

export const userListSchema = z.array(userSchema);

export type User = z.infer<typeof userSchema>;
export type Session = z.infer<typeof sessionSchema>;
