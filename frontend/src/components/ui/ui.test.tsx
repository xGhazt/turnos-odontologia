import { render, screen } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { MemoryRouter } from 'react-router-dom';
import { describe, expect, it, vi } from 'vitest';
import { Alert } from './Alert';
import { Button } from './Button';
import { ConfirmDialog } from './ConfirmDialog';
import { Spinner } from './Spinner';
import { TextField } from './TextField';
import { Toast } from './Toast';
import { ModulePlaceholder } from '../../pages/ModulePlaceholder';
import { NotFoundPage } from '../../pages/NotFoundPage';
import { ForbiddenView } from '../../pages/ForbiddenView';

describe('Button', () => {
  it('expone aria-busy y queda deshabilitado mientras carga', () => {
    render(<Button loading>Ingresar</Button>);
    const button = screen.getByRole('button', { name: /ingresar/i });
    expect(button).toBeDisabled();
    expect(button).toHaveAttribute('aria-busy', 'true');
  });
});

describe('TextField', () => {
  it('asocia la etiqueta y el mensaje de error al campo', () => {
    render(<TextField label="Email" error="El email es obligatorio." value="" onChange={() => {}} />);
    const input = screen.getByLabelText('Email');
    expect(input).toHaveAttribute('aria-invalid', 'true');
    expect(input).toHaveAttribute('aria-describedby', 'field-email-error');
    expect(screen.getByText('El email es obligatorio.')).toBeInTheDocument();
  });

  it('muestra el hint cuando no hay error', () => {
    render(<TextField label="Email" hint="Usá un correo ficticio." value="" onChange={() => {}} />);
    expect(screen.getByText('Usá un correo ficticio.')).toBeInTheDocument();
  });
});

describe('Alert', () => {
  it('usa role alert para errores y status para información', () => {
    const { rerender } = render(<Alert variant="error">Falló</Alert>);
    expect(screen.getByRole('alert')).toHaveTextContent('Falló');

    rerender(<Alert variant="info">Sesión expirada</Alert>);
    expect(screen.getByRole('status')).toHaveTextContent('Sesión expirada');
  });
});

describe('Spinner', () => {
  it('anuncia el estado de carga con role status', () => {
    render(<Spinner label="Verificando sesión…" />);
    expect(screen.getByRole('status')).toHaveTextContent('Verificando sesión…');
  });
});

describe('ConfirmDialog', () => {
  it('enfoca una acción al abrir y cierra con Escape', async () => {
    const user = userEvent.setup();
    const onCancel = vi.fn();
    render(
      <ConfirmDialog
        open
        title="¿Cerrar sesión?"
        onConfirm={() => {}}
        onCancel={onCancel}
      />,
    );

    expect(screen.getByRole('dialog')).toBeInTheDocument();
    expect(screen.getByRole('button', { name: 'Cancelar' })).toHaveFocus();

    await user.keyboard('{Escape}');
    expect(onCancel).toHaveBeenCalled();
  });
});

describe('Toast', () => {
  it('anuncia el mensaje y permite cerrarlo', async () => {
    const user = userEvent.setup();
    const onClose = vi.fn();
    render(<Toast message="Guardado" variant="success" onClose={onClose} />);

    expect(screen.getByRole('status')).toHaveTextContent('Guardado');
    await user.click(screen.getByRole('button', { name: /cerrar notificación/i }));
    expect(onClose).toHaveBeenCalled();
  });
});

describe('Páginas de estado', () => {
  it('ModulePlaceholder muestra el título y no renderiza tablas', () => {
    render(
      <MemoryRouter>
        <ModulePlaceholder title="Agenda" change="C-12" />
      </MemoryRouter>,
    );
    expect(screen.getByRole('heading', { name: 'Agenda' })).toBeInTheDocument();
    expect(screen.getByText(/change posterior/i)).toBeInTheDocument();
    expect(screen.queryByRole('table')).not.toBeInTheDocument();
  });

  it('NotFoundPage muestra el título y la acción de volver', () => {
    render(
      <MemoryRouter>
        <NotFoundPage />
      </MemoryRouter>,
    );
    expect(screen.getByRole('heading', { name: /página no encontrada/i })).toBeInTheDocument();
    expect(screen.getByRole('link', { name: /volver al inicio/i })).toBeInTheDocument();
  });

  it('ForbiddenView muestra el acceso denegado y la acción de volver', () => {
    render(
      <MemoryRouter>
        <ForbiddenView />
      </MemoryRouter>,
    );
    expect(screen.getByRole('heading', { name: /acceso denegado/i })).toBeInTheDocument();
    expect(screen.getByRole('link', { name: /volver al inicio/i })).toBeInTheDocument();
  });
});
