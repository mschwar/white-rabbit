import { render, screen } from '@testing-library/react'
import { expect, test } from 'vitest'
import Page from '../page'

test('renders get started link', () => {
  render(<Page />)
  expect(screen.getByText(/get started/i)).toBeDefined()
})
