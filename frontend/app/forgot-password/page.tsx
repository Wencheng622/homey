import { Metadata } from 'next';
import ForgotPasswordForm from './ForgotPasswordForm';

export const metadata: Metadata = {
  title: 'Forgot Password - Home In',
  description: 'Reset your Home In account password',
};

export default function ForgotPasswordPage() {
  return <ForgotPasswordForm />;
}
