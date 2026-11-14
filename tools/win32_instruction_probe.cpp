// OWN disposable IA32 method fixture. No TSE headers, libraries or game data.
// Root builds with the installed MSVC x86 toolchain. Never built by this agent.
// Kernel32 only: /GS- /GR- /EHs-c- /Zl, /NODEFAULTLIB /ENTRY:ProbeEntry.
#include <windows.h>

#if !defined(_M_IX86)
#error This fixture requires native Win32 IA32 code, not ELF or x64.
#endif

extern "C" __declspec(naked) void __stdcall ProbeSavedMidpoint(DWORD) {
  __asm {
    nop
    nop
    nop
    nop
    nop
    nop
    nop
    nop
    pop edi
    pop esi
    pop ebx
    mov esp, ebp
    pop ebp
    ret 4
  }
}

extern "C" __declspec(naked) void __stdcall ProbeSaved(DWORD) {
  __asm {
    push ebp
    mov ebp, esp
    sub esp, 130h
    push ebx
    push esi
    push edi
    jmp ProbeSavedMidpoint
  }
}

extern "C" __declspec(naked) DWORD __stdcall InvokeSaved() {
  __asm {
    push edi
    mov edi, 12345678h
    push 0
    call ProbeSaved
    mov eax, edi
    pop edi
    ret
  }
}

extern "C" __declspec(naked) DWORD __stdcall ProbeArguments(DWORD, DWORD) {
  __asm {
    mov eax, [esp+4]
    xor eax, [esp+8]
    ret 8
  }
}

// Reached by JMP, not CALL. ESP points to argument1, not a return address.
extern "C" __declspec(naked) DWORD __stdcall ProbeArgumentMidpoint() {
  __asm {
    nop
    nop
    nop
    nop
    nop
    nop
    nop
    nop
    call ProbeArguments
    ret
  }
}

extern "C" __declspec(naked) DWORD __stdcall InvokeArguments() {
  __asm {
    push 01020304h
    push 11223344h
    jmp ProbeArgumentMidpoint
  }
}

static DWORD length(const char* text) {
  DWORD n=0;while(text[n])++n;return n;
}
static BOOL output(const char* text) {
  DWORD done=0;const DWORD n=length(text);
  return WriteFile(GetStdHandle(STD_OUTPUT_HANDLE),text,n,&done,NULL)&&done==n;
}
static void hex(DWORD value,char* out) {
  const char* digits="0123456789abcdef";
  for(unsigned i=0;i<8;++i)out[i]=digits[(value>>(28-4*i))&15];
}
struct CommandRead { char byte;DWORD done;BOOL ok; };

static DWORD WINAPI CommandReader(void* opaque) {
  CommandRead* read=(CommandRead*)opaque;
  read->ok=ReadFile(GetStdHandle(STD_INPUT_HANDLE),&read->byte,1,&read->done,NULL);
  return 0;
}

static BOOL command(char wanted) {
  CommandRead state={0,0,FALSE};
  HANDLE thread=CreateThread(NULL,0,CommandReader,&state,0,NULL);
  if(thread==NULL)return FALSE;
  const DWORD waited=WaitForSingleObject(thread,15000);
  if(waited!=WAIT_OBJECT_0)ExitProcess(12);
  if(!CloseHandle(thread))return FALSE;
  return state.ok&&state.done==1&&state.byte==wanted;
}

static char resultRow[]="{\"phase\":\"WAIT_CLEANUP\",\"saved_edi\":\"00000000\",\"argument_result\":\"00000000\"}\n";

extern "C" void ProbeEntry() {
  if(!output("{\"phase\":\"READY\",\"schema\":1}\n")||!command('R'))ExitProcess(10);
  const DWORD saved=InvokeSaved();
  const DWORD args=InvokeArguments();
  // All tested native frames have returned. Neither site is executed again.
  char* field=resultRow;
  while(*field&&!(field[0]=='0'&&field[1]=='0'))++field;
  hex(saved,field);field+=8;
  while(*field&&!(field[0]=='0'&&field[1]=='0'))++field;
  hex(args,field);
  if(!output(resultRow)||!command('Q'))ExitProcess(11);
  ExitProcess(0);
}
