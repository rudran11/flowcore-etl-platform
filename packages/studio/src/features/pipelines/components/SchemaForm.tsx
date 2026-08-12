import React, { useState } from 'react';
import { Input } from '../../../components/ui/input';
import { Eye, EyeOff } from 'lucide-react';

interface SchemaFormProps {
  schema: any;
  formData: any;
  onChange: (key: string, value: any) => void;
  setIsValid?: (isValid: boolean) => void;
}

export const SchemaForm: React.FC<SchemaFormProps> = ({ schema, formData, onChange, setIsValid }) => {
  const [showSecrets, setShowSecrets] = useState<Record<string, boolean>>({});
  
  if (!schema || !schema.properties) {
    // If no schema, valid by default
    React.useEffect(() => { setIsValid?.(true); }, [setIsValid]);
    return <div className="text-sm text-muted-foreground p-4">No configuration schema available.</div>;
  }

  const properties = schema.properties;
  const requiredFields = schema.required || [];
  
  let hasErrors = false;

  const renderFields = () => {
    return Object.entries(properties).map(([key, prop]: [string, any]) => {
      const isRequired = requiredFields.includes(key);
      const value = formData[key] ?? prop.default ?? '';
      const isSecret = prop.format === 'password' || key.toLowerCase().includes('password') || key.toLowerCase().includes('token') || key.toLowerCase().includes('secret');
      const showSecret = showSecrets[key] || false;
      
      let error = null;
      if (isRequired && (value === undefined || value === null || value === '')) {
        error = 'This field is required';
        hasErrors = true;
      }

      const renderInput = () => {
        if (prop.enum || prop.json_schema_extra?.enum) {
          const enumValues = prop.enum || prop.json_schema_extra?.enum;
          return (
            <select
              value={value}
              onChange={(e) => onChange(key, e.target.value)}
              className="w-full h-10 px-3 rounded-md bg-zinc-900 border border-white/10 text-sm text-white focus:outline-none focus:ring-2 focus:ring-primary"
            >
              <option value="" disabled>Select an option</option>
              {enumValues.map((opt: string) => (
                <option key={opt} value={opt}>{opt}</option>
              ))}
            </select>
          );
        }
        
        if (prop.type === 'boolean') {
          return (
            <div className="flex items-center gap-2 mt-2">
              <input 
                type="checkbox"
                checked={value === true}
                onChange={(e) => onChange(key, e.target.checked)}
                className="w-4 h-4 rounded border-white/10 bg-zinc-900"
              />
              <span className="text-sm text-zinc-300">Enable</span>
            </div>
          );
        }
        
        if (prop.format === 'multiline' || prop.json_schema_extra?.format === 'multiline') {
          return (
            <textarea
              value={value}
              onChange={(e) => onChange(key, e.target.value)}
              placeholder={prop.placeholder || prop.json_schema_extra?.placeholder || ''}
              className="w-full min-h-[100px] px-3 py-2 rounded-md bg-zinc-900 border border-white/10 text-sm text-white focus:outline-none focus:ring-2 focus:ring-primary font-mono mt-1"
            />
          );
        }

        if (isSecret) {
          return (
            <div className="relative mt-1">
              <Input
                type={showSecret ? "text" : "password"}
                value={value}
                onChange={(e) => onChange(key, e.target.value)}
                placeholder={prop.placeholder || prop.json_schema_extra?.placeholder || '********'}
                className="bg-zinc-900 border-white/10 pr-10"
              />
              <button
                type="button"
                onClick={() => setShowSecrets(prev => ({ ...prev, [key]: !prev[key] }))}
                className="absolute right-3 top-1/2 -translate-y-1/2 text-zinc-500 hover:text-zinc-300"
              >
                {showSecret ? <EyeOff className="w-4 h-4" /> : <Eye className="w-4 h-4" />}
              </button>
            </div>
          );
        }
        
        return (
          <Input
            type={prop.type === 'integer' || prop.type === 'number' ? 'number' : 'text'}
            value={value}
            onChange={(e) => {
              const val = e.target.value;
              if (prop.type === 'integer' || prop.type === 'number') {
                onChange(key, val === '' ? '' : Number(val));
              } else {
                onChange(key, val);
              }
            }}
            placeholder={prop.placeholder || prop.json_schema_extra?.placeholder || ''}
            className="bg-zinc-900 border-white/10 mt-1"
          />
        );
      };

      return (
        <div key={key} className="space-y-1">
          <label className="flex items-center gap-1 text-sm font-medium text-zinc-300">
            {prop.title || key}
            {isRequired && <span className="text-red-500">*</span>}
          </label>
          {prop.description && (
            <p className="text-xs text-zinc-500">{prop.description}</p>
          )}
          {renderInput()}
          {error && <p className="text-xs text-red-500 mt-1">{error}</p>}
        </div>
      );
    });
  };

  const fields = renderFields();
  
  React.useEffect(() => {
    setIsValid?.(!hasErrors);
  }, [hasErrors, setIsValid]);

  return (
    <div className="space-y-5 p-4">
      {fields}
    </div>
  );
};
