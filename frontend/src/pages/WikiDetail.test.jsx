/**
 * TDD: WikiDetail CRUD Tests
 *
 * Test Coverage:
 * - CREATE: 새 문서 작성 모드 (2 tests)
 * - READ: 기존 문서 조회 (2 tests)
 * - UPDATE: 문서 수정 (2 tests)
 * - DELETE: 문서 삭제 (1 test)
 *
 * Total: 7 tests
 */
import { describe, it, expect, vi, beforeEach } from 'vitest';
import { render, screen, waitFor } from '@testing-library/react';
import { userEvent } from '@testing-library/user-event';
import { BrowserRouter } from 'react-router-dom';
import WikiDetail from './WikiDetail';
import * as api from '../services/api';

// Default mock for useParams
const mockUseParams = vi.fn(() => ({
  projectId: 'test-project',
  docSlug: 'test-doc',
  category: 'test'
}));

const mockUseNavigate = vi.fn();

// Mock React Router
vi.mock('react-router-dom', async () => {
  const actual = await vi.importActual('react-router-dom');
  return {
    ...actual,
    useParams: mockUseParams,
    useNavigate: () => mockUseNavigate,
  };
});

// Mock API
vi.mock('../services/api');

describe('WikiDetail - CREATE Tests', () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  it('Test 1: 새 문서 작성 모드 렌더링', async () => {
    /**
     * Given: docSlug이 'new'
     * When: WikiDetail 컴포넌트 렌더링
     * Then: 편집 모드 활성화, 기본 텍스트 표시
     */
    mockUseParams.mockReturnValue({
      projectId: 'test',
      docSlug: 'new',
      category: 'characters'
    });

    render(
      <BrowserRouter>
        <WikiDetail />
      </BrowserRouter>
    );

    await waitFor(() => {
      const textarea = screen.getByPlaceholderText('# 제목을 입력하세요...');
      expect(textarea).toBeInTheDocument();
      expect(textarea).toHaveValue('# 새로운 문서\n\n여기에 내용을 입력하세요.');
    });
  });

  it('Test 2: 새 문서 저장', async () => {
    /**
     * Given: 새 문서 작성 모드
     * When: 제목과 내용을 입력하고 저장 버튼 클릭
     * Then: createPage API 호출
     */
    const user = userEvent.setup();
    const mockCreatePage = vi.mocked(api.createPage);
    mockCreatePage.mockResolvedValue({
      slug: 'test/new-doc',
      title: 'New Document',
      content: '# New Document',
      id: 1,
      created_at: '2026-01-11'
    });

    mockUseParams.mockReturnValue({
      projectId: 'test',
      docSlug: 'new',
      category: 'test'
    });

    render(
      <BrowserRouter>
        <WikiDetail />
      </BrowserRouter>
    );

    await waitFor(() => {
      expect(screen.getByPlaceholderText('# 제목을 입력하세요...')).toBeInTheDocument();
    });

    // Enter title
    const titleInput = screen.getByPlaceholderText('Document Title');
    await user.clear(titleInput);
    await user.type(titleInput, 'New Document');

    // Enter content
    const contentTextarea = screen.getByPlaceholderText('# 제목을 입력하세요...');
    await user.clear(contentTextarea);
    await user.type(contentTextarea, '# New Document{enter}Content here');

    // Click save button
    const saveButton = screen.getByText('Save Changes');
    await user.click(saveButton);

    await waitFor(() => {
      expect(mockCreatePage).toHaveBeenCalledWith(
        expect.objectContaining({
          title: 'New Document',
          content: expect.stringContaining('New Document')
        })
      );
    });
  });
});

describe('WikiDetail - READ Tests', () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  it('Test 3-1: 카테고리 기반 slug로 문서 조회 (BUG)', async () => {
    /**
     * Given: URL이 /wiki/characters/테스트 형태
     * When: WikiDetail 컴포넌트 마운트
     * Then: getPage가 전체 slug "characters/테스트"로 호출되어야 함
     *
     * 현재 버그: getPage가 "테스트"로만 호출됨 → 404 발생
     */
    mockUseParams.mockReturnValue({
      projectId: 'test-project',
      category: 'characters',
      docSlug: '테스트'
    });

    const mockPage = {
      slug: 'characters/테스트',
      title: '테스트 문서',
      content: '# 테스트\n\n내용',
      github_sha: 'abc123',
      created_at: '2026-01-17',
      updated_at: '2026-01-17'
    };

    vi.mocked(api.getPage).mockResolvedValue(mockPage);

    render(
      <BrowserRouter>
        <WikiDetail />
      </BrowserRouter>
    );

    await waitFor(() => {
      // 버그: getPage가 "테스트"로 호출됨
      // 수정 후: getPage가 "characters/테스트"로 호출되어야 함
      expect(api.getPage).toHaveBeenCalledWith('characters/테스트');
    });
  });

  it('Test 3: 기존 문서 조회', async () => {
    /**
     * Given: 존재하는 문서 slug
     * When: WikiDetail 컴포넌트 마운트
     * Then: getPage API 호출, 문서 내용 표시
     */
    const mockPage = {
      slug: 'test/existing-doc',
      title: 'Existing Document',
      content: '# Existing Document\n\nThis is content.',
      github_sha: 'abc123',
      created_at: '2026-01-10',
      updated_at: '2026-01-11'
    };

    vi.mocked(api.getPage).mockResolvedValue(mockPage);

    render(
      <BrowserRouter>
        <WikiDetail />
      </BrowserRouter>
    );

    await waitFor(() => {
      expect(api.getPage).toHaveBeenCalledWith('test-doc');
      // Use getAllByText and check the first one (title)
      const titles = screen.getAllByText('Existing Document');
      expect(titles.length).toBeGreaterThan(0);
    });
  });

  it('Test 4: 문서 조회 실패 (404)', async () => {
    /**
     * Given: 존재하지 않는 문서 slug
     * When: WikiDetail 컴포넌트 마운트
     * Then: 에러 메시지 표시
     */
    vi.mocked(api.getPage).mockRejectedValue({
      response: {
        data: {
          detail: { message: 'Document not found' }
        }
      }
    });

    render(
      <BrowserRouter>
        <WikiDetail />
      </BrowserRouter>
    );

    await waitFor(() => {
      expect(screen.getByText('Failed to load document')).toBeInTheDocument();
    });
  });
});

describe('WikiDetail - UPDATE Tests', () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  it('Test 5: 문서 수정', async () => {
    /**
     * Given: 기존 문서를 불러온 상태
     * When: Edit 버튼 클릭 → 내용 수정 → Save 버튼 클릭
     * Then: updatePage API 호출
     */
    const user = userEvent.setup();
    const mockPage = {
      slug: 'test/doc',
      title: 'Original Title',
      content: '# Original',
      github_sha: 'sha123',
      status: 'active',
      summary: '',
      tags: []
    };

    vi.mocked(api.getPage).mockResolvedValue(mockPage);
    vi.mocked(api.updatePage).mockResolvedValue({
      ...mockPage,
      title: 'Updated Title',
      content: '# Updated'
    });

    render(
      <BrowserRouter>
        <WikiDetail />
      </BrowserRouter>
    );

    // Wait for document to load
    await waitFor(() => {
      expect(screen.getByText('Original Title')).toBeInTheDocument();
    });

    // Click Edit button
    const editButton = screen.getByText('Edit');
    await user.click(editButton);

    // Modify title
    const titleInput = screen.getByDisplayValue('Original Title');
    await user.clear(titleInput);
    await user.type(titleInput, 'Updated Title');

    // Click Save
    const saveButton = screen.getByText('Save Changes');
    await user.click(saveButton);

    await waitFor(() => {
      expect(api.updatePage).toHaveBeenCalledWith(
        'test-doc',
        expect.objectContaining({
          title: 'Updated Title',
          expected_sha: 'sha123'
        })
      );
    });
  });

  it('Test 6: 저장 중 입력 비활성화', async () => {
    /**
     * Given: 문서 수정 중
     * When: Save 버튼 클릭 (저장 중)
     * Then: MarkdownEditor disabled prop = true
     */
    const user = userEvent.setup();
    const mockPage = {
      slug: 'test/doc',
      title: 'Title',
      content: '# Content',
      github_sha: 'sha123',
      status: 'active',
      summary: '',
      tags: []
    };

    vi.mocked(api.getPage).mockResolvedValue(mockPage);
    vi.mocked(api.updatePage).mockImplementation(() =>
      new Promise(resolve => setTimeout(() => resolve(mockPage), 1000))
    );

    render(
      <BrowserRouter>
        <WikiDetail />
      </BrowserRouter>
    );

    await waitFor(() => {
      expect(screen.getByText('Title')).toBeInTheDocument();
    });

    // Enter edit mode
    await user.click(screen.getByText('Edit'));

    // Click save
    await user.click(screen.getByText('Save Changes'));

    // Check if Save button shows "Saving..."
    await waitFor(() => {
      expect(screen.getByText('Saving...')).toBeInTheDocument();
    });

    // Check if textarea is disabled
    const textarea = screen.getByPlaceholderText('# 제목을 입력하세요...');
    expect(textarea).toBeDisabled();
  });
});

describe('WikiDetail - DELETE Tests', () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  it('Test 7: 문서 삭제', async () => {
    /**
     * Given: 기존 문서를 불러온 상태
     * When: 삭제 버튼 클릭 → 확인 → 삭제
     * Then: deletePage API 호출
     */
    const user = userEvent.setup();
    const mockPage = {
      slug: 'test/doc-to-delete',
      title: 'To Delete',
      content: '# Delete Me',
      github_sha: 'sha123',
      status: 'active',
      summary: '',
      tags: []
    };

    vi.mocked(api.getPage).mockResolvedValue(mockPage);
    vi.mocked(api.deletePage).mockResolvedValue({ success: true });

    // Mock window.confirm
    global.confirm = vi.fn(() => true);

    render(
      <BrowserRouter>
        <WikiDetail />
      </BrowserRouter>
    );

    await waitFor(() => {
      expect(screen.getByText('To Delete')).toBeInTheDocument();
    });

    // Find and click delete button (trash icon button)
    const deleteButton = screen.getByRole('button', { name: '' });  // Icon button
    await user.click(deleteButton);

    await waitFor(() => {
      expect(api.deletePage).toHaveBeenCalledWith('test-doc', false);
      expect(global.confirm).toHaveBeenCalled();
    });
  });
});
