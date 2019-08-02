# IrisSplitter

## IrisSplitter 의 필수 Property 목록
- **log_suffix** : log 이름은 `<ProcessName>-<Suffix>.log.<number>` 로  되는데 여기서 suffix를 지정

## IrisLoader에서 처리해야할 FlowFile의 필수 Attribute 목록
- **storage_type** : split된 결과가 저장되는 경로에 디렉토리명을 구분하기위해 사용. file에서 가져온건지, 다른 db에서 가져온건지 기술 할 수 있음. **save_path**의 하위 경로 이름이 됨.
- **tablename** : 최종적으로 load할 테이블이름을 지정
- **key_column_name** : load할 때 필요한 key column의 이름을 지정
- **partition_column_name** : load할 때 필요한 partition column의 이름을 지정
- **save_path** : split된 결과가 저장될 경로를 지정
- **field_seperator** : split된 결과가 저장될 때의 필드 구분자 지정
