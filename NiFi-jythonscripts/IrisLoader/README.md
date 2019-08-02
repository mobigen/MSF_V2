# IrisLoader
## IrisLoader의 필수 Property 목록
- **error_path** : Load에 실패한 파일들을 따로 보관할 장소
- **field_sep** : Load할 파일의 필드 구분자를 지정
- **record_sep** : Load할 파일의 레코드 구분자를 지정
- **log_suffix** : log 이름은 `<ProcessName>-<Suffix>.log.<number>` 로  되는데 여기서 suffix를 지정
- **process_id** : 해당 프로세서의 process_id를 지정, 나중에 프로세스의 메타정보를 가져오는데 쓰임
- **remove** : Load한 파일을 지울지를 결정 옵션은 "True", "False" 만 가능

## IrisLoader에서 처리해야할 FlowFile의 필수 Attribute 목록
UpdateAttribute 프로세서를 통해 미리 FlowFile에Attribute들을 첨부해야 함.

- **tablename** : 로드 대상이 될 Table 이름
- **key** : 로드 key value
- **partition** : 로드 partition value
- **dat_path** : 로드 할 파일의 dat파일 경로
- **ctl_path** : 로드 할 파일의 ctl파일 경로
