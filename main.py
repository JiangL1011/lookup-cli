import sys
import os
import click
from app.cli import cli


def main():
    """Main entry point that handles subcommand routing."""
    # 设置Windows控制台编码支持
    if sys.platform == "win32":
        # 尝试设置控制台为UTF-8模式
        try:
            import codecs
            if hasattr(sys.stdout, 'reconfigure'):
                sys.stdout.reconfigure(encoding='utf-8')
            if hasattr(sys.stderr, 'reconfigure'):
                sys.stderr.reconfigure(encoding='utf-8')
        except Exception:
            # 如果重配置失败，设置环境变量
            os.environ.setdefault('PYTHONIOENCODING', 'utf-8')
    
    # 检查第一个参数是否是子命令
    if len(sys.argv) > 1:
        first_arg = sys.argv[1]
        
        if first_arg in ['init', 'trans']:
            # 直接调用子命令
            cmd = cli.commands.get(first_arg)
            if cmd:
                # 创建Context并调用命令
                ctx = click.Context(cli)
                sub_ctx = click.Context(cmd, parent=ctx)
                
                # 解析其余参数
                remaining_args = sys.argv[2:]
                try:
                    if first_arg == 'init':
                        # init命令不需要参数
                        cmd.invoke(sub_ctx)
                    elif first_arg == 'trans':
                        # 检查是否是help请求
                        if '--help' in remaining_args or '-h' in remaining_args:
                            click.echo(cmd.get_help(sub_ctx))
                            return
                        
                        # trans命令需要解析参数
                        # 这里我们需要手动解析参数
                        target = None
                        text_parts = []
                        
                        i = 0
                        while i < len(remaining_args):
                            arg = remaining_args[i]
                            if arg in ['-t', '--target']:
                                if i + 1 < len(remaining_args):
                                    target = remaining_args[i + 1]
                                    i += 2
                                else:
                                    i += 1
                            else:
                                text_parts.append(arg)
                                i += 1
                        
                        # 调用trans命令
                        sub_ctx.params = {'target': target, 'text': text_parts}
                        cmd.invoke(sub_ctx)
                    return
                except SystemExit:
                    return
    
    # 如果不是子命令，正常调用CLI
    cli()


if __name__ == "__main__":
    main()
