"""
GitHub API 클라이언트
"""
from github import Github, GithubException
from app.core.config import settings
import base64
from typing import Optional, Dict, Any
import frontmatter
import structlog

logger = structlog.get_logger()


class GitHubClient:
    """GitHub Repository 관리 클라이언트"""

    def __init__(self):
        self.client = Github(settings.GITHUB_TOKEN)
        self.repo = self.client.get_repo(settings.GITHUB_REPO)
        self.branch = settings.GITHUB_BRANCH

    def get_file(self, path: str) -> Optional[Dict[str, Any]]:
        """
        GitHub에서 파일 가져오기

        Returns:
            {
                "content": str,  # 디코딩된 내용
                "sha": str,      # 파일 SHA
                "url": str       # GitHub URL
            }
        """
        try:
            file_path = f"content/{path}.md" if not path.endswith(".md") else f"content/{path}"
            file_content = self.repo.get_contents(file_path, ref=self.branch)

            # 바이너리 디코딩
            content = base64.b64decode(file_content.content).decode("utf-8")

            return {
                "content": content,
                "sha": file_content.sha,
                "url": file_content.html_url,
            }
        except GithubException as e:
            if e.status == 404:
                logger.warning("github_file_not_found", path=path)
                return None
            logger.error("github_api_error", path=path, status=e.status, error=str(e))
            raise

    def create_file(
        self,
        path: str,
        content: str,
        message: str,
        author_name: Optional[str] = None,
        is_binary: bool = False
    ) -> Dict[str, Any]:
        """
        GitHub에 새 파일 생성

        Args:
            path: 파일 경로 (content/ 제외)
            content: 파일 내용 (is_binary=True이면 base64 인코딩된 문자열)
            message: 커밋 메시지
            author_name: 작성자 이름
            is_binary: 바이너리 파일 여부 (이미지 등)

        Returns:
            {
                "sha": str,
                "commit_sha": str,
                "url": str
            }
        """
        try:
            # 바이너리 파일은 경로 그대로 사용 (content/ 접두사 없음)
            # 마크다운 파일은 content/ 추가
            if is_binary:
                file_path = path
            else:
                file_path = f"content/{path}.md" if not path.endswith(".md") else f"content/{path}"

            # 커밋
            result = self.repo.create_file(
                path=file_path,
                message=message,
                content=content,
                branch=self.branch
            )

            logger.info("github_file_created", path=path, sha=result["content"].sha, binary=is_binary)

            return {
                "sha": result["content"].sha,
                "commit_sha": result["commit"].sha,
                "url": result["content"].html_url,
            }
        except GithubException as e:
            logger.error("github_create_failed", path=path, status=e.status, error=str(e))
            raise

    def update_file(
        self,
        path: str,
        content: str,
        message: str,
        sha: str,
        author_name: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        GitHub 파일 업데이트

        Args:
            path: 파일 경로
            content: 새 내용
            message: 커밋 메시지
            sha: 현재 파일 SHA (동시성 제어)
            author_name: 작성자 이름

        Returns:
            {
                "sha": str,  # 새 파일 SHA
                "commit_sha": str,
                "url": str
            }

        Raises:
            GithubException: SHA 불일치 시 409 에러
        """
        try:
            file_path = f"content/{path}.md" if not path.endswith(".md") else f"content/{path}"

            result = self.repo.update_file(
                path=file_path,
                message=message,
                content=content,
                sha=sha,
                branch=self.branch
            )

            logger.info("github_file_updated", path=path, old_sha=sha, new_sha=result["content"].sha)

            return {
                "sha": result["content"].sha,
                "commit_sha": result["commit"].sha,
                "url": result["content"].html_url,
            }
        except GithubException as e:
            if e.status == 409:
                logger.warning("github_conflict", path=path, sha=sha)
            else:
                logger.error("github_update_failed", path=path, status=e.status, error=str(e))
            raise

    def delete_file(
        self,
        path: str,
        message: str,
        sha: str
    ) -> Dict[str, Any]:
        """
        GitHub 파일 삭제

        Args:
            path: 파일 경로
            message: 커밋 메시지
            sha: 파일 SHA

        Returns:
            {"commit_sha": str}
        """
        try:
            file_path = f"content/{path}.md" if not path.endswith(".md") else f"content/{path}"

            result = self.repo.delete_file(
                path=file_path,
                message=message,
                sha=sha,
                branch=self.branch
            )

            logger.info("github_file_deleted", path=path, sha=sha)

            return {"commit_sha": result["commit"].sha}
        except GithubException as e:
            logger.error("github_delete_failed", path=path, status=e.status, error=str(e))
            raise

    def move_file(
        self,
        old_path: str,
        new_path: str,
        message: str,
        sha: str
    ) -> Dict[str, Any]:
        """
        파일 이동 (archived 폴더로 이동 등)

        실제로는 삭제 후 생성
        """
        # 1. 원본 파일 가져오기
        file_data = self.get_file(old_path)
        if not file_data:
            raise FileNotFoundError(f"File not found: {old_path}")

        # 2. 새 위치에 생성
        create_result = self.create_file(
            path=new_path,
            content=file_data["content"],
            message=message
        )

        # 3. 원본 삭제
        self.delete_file(
            path=old_path,
            message=f"Moved to {new_path}",
            sha=sha
        )

        return create_result


# 전역 클라이언트 인스턴스
github_client = GitHubClient()
