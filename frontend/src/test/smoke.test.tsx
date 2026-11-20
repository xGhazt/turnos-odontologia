import { render, screen } from '@testing-library/react';
import { MemoryRouter } from 'react-router-dom';
import { describe, expect, it } from 'vitest';
import { Brand } from '../components/ui/Brand';

describe('shell smoke test', () => {
  it('renderiza la marca como enlace accesible', () => {
    render(
      <MemoryRouter>
        <Brand />
      </MemoryRouter>,
    );

    expect(screen.getByRole('link', { name: /turnos odontología/i })).toBeInTheDocument();
  });
});
