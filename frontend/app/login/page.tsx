import { Metadata } from 'next';
import LoginForm from './LoginForm';

export const metadata: Metadata = {
  title: 'Sign In - Home In',
  description: 'Login to your Home In account to find your perfect rental property',
};

async function getLoginConfig() {
  return {
    enableGoogleLogin: true,
    enableForgotPassword: true,
  };
}

export default async function LoginPage() {
  const config = await getLoginConfig();
  
  return (
    <>
      <LoginForm config={config} />
    </>
  );
}