'use client';

export type AuthRole = 'tenant' | 'landlord';

interface RoleToggleProps {
  role: AuthRole;
  onChange: (role: AuthRole) => void;
  tenantLabel?: string;
  landlordLabel?: string;
}

export default function RoleToggle({
  role,
  onChange,
  tenantLabel = 'Tenant',
  landlordLabel = 'Landlord',
}: RoleToggleProps) {
  return (
    <div className="flex gap-3 bg-orange-50/80 p-1.5 rounded-full border border-orange-100 mb-7">
      <button
        type="button"
        onClick={() => onChange('tenant')}
        className={`flex-1 flex items-center justify-center gap-2 py-3 rounded-full font-semibold text-sm transition-all duration-200 ${
          role === 'tenant'
            ? 'bg-orange-400 text-orange-950 shadow-sm'
            : 'text-orange-800 hover:bg-orange-100'
        }`}
      >
        <i className="fas fa-user-friends" />
        <span>{tenantLabel}</span>
      </button>
      <button
        type="button"
        onClick={() => onChange('landlord')}
        className={`flex-1 flex items-center justify-center gap-2 py-3 rounded-full font-semibold text-sm transition-all duration-200 ${
          role === 'landlord'
            ? 'bg-orange-400 text-orange-950 shadow-sm'
            : 'text-orange-800 hover:bg-orange-100'
        }`}
      >
        <i className="fas fa-home" />
        <span>{landlordLabel}</span>
      </button>
    </div>
  );
}
