import { Metadata } from 'next';
import RegisterForm from './RegisterForm';

export const metadata: Metadata = {
  title: 'Create Account - Home In',
  description: 'Join Home In to find your perfect rental property',
};

export default async function RegisterPage() {
  return <RegisterForm />;
}