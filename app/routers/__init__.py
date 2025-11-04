# FastAPI 라우터를 쉽게 임포트할 수 있도록 빈 파일로 유지하거나 필요한 라우터를 임포트할 수 있습니다.
# 여기서는 라우터 폴더를 패키지로 인식하게 하는 역할만 수행합니다.

from . import study_guide
# ... 다른 라우터들 (applications, auth, interview 등)