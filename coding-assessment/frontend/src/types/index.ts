export type User = {
  id: string;
  email: string;
  name: string;
  role: string;
};

export type LiveEvent = {
  _id: string;
  body: string;
  authorId: string;
  createdAt: string;
};

export type ApiError = {
  message: string;
};
