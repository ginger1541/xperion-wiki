import { describe, it, expect, vi } from 'vitest';
import { render, screen } from '@testing-library/react';
import { userEvent } from '@testing-library/user-event';
import { MarkdownEditor } from './MarkdownEditor';

describe('MarkdownEditor', () => {
  it('should render textarea with initial content', () => {
    const content = '# Test Content';
    const onChange = vi.fn();

    render(<MarkdownEditor content={content} onChange={onChange} />);

    const textarea = screen.getByPlaceholderText('# 제목을 입력하세요...');
    expect(textarea).toBeInTheDocument();
    expect(textarea).toHaveValue(content);
  });

  it('should call onChange when user types', async () => {
    const user = userEvent.setup();
    const content = '';
    const onChange = vi.fn();

    render(<MarkdownEditor content={content} onChange={onChange} />);

    const textarea = screen.getByPlaceholderText('# 제목을 입력하세요...');
    await user.type(textarea, 'New content');

    expect(onChange).toHaveBeenCalled();
  });

  it('should disable textarea when disabled prop is true', () => {
    const content = '# Test Content';
    const onChange = vi.fn();

    render(<MarkdownEditor content={content} onChange={onChange} disabled={true} />);

    const textarea = screen.getByPlaceholderText('# 제목을 입력하세요...');
    expect(textarea).toBeDisabled();
  });

  it('should enable textarea when disabled prop is false', () => {
    const content = '# Test Content';
    const onChange = vi.fn();

    render(<MarkdownEditor content={content} onChange={onChange} disabled={false} />);

    const textarea = screen.getByPlaceholderText('# 제목을 입력하세요...');
    expect(textarea).not.toBeDisabled();
  });

  it('should enable textarea by default when disabled prop is not provided', () => {
    const content = '# Test Content';
    const onChange = vi.fn();

    render(<MarkdownEditor content={content} onChange={onChange} />);

    const textarea = screen.getByPlaceholderText('# 제목을 입력하세요...');
    expect(textarea).not.toBeDisabled();
  });

  it('should not call onChange when disabled and user tries to type', async () => {
    const user = userEvent.setup();
    const content = '# Original Content';
    const onChange = vi.fn();

    render(<MarkdownEditor content={content} onChange={onChange} disabled={true} />);

    const textarea = screen.getByPlaceholderText('# 제목을 입력하세요...');

    // Try to type (should not work because it's disabled)
    await user.type(textarea, 'New content');

    // onChange should not be called because textarea is disabled
    expect(onChange).not.toHaveBeenCalled();
  });
});
