tmux new-window -t cs525 -n win1 "ssh cs525-01"; \
tmux split-window -h -t cs525:win1 "ssh cs525-02"; \
tmux split-window -v -t cs525:win1.0 "ssh cs525-03"; \
tmux split-window -v -t cs525:win1.1 "ssh cs525-04"; \
tmux select-layout -t cs525:win1 tiled; \
tmux new-window -t cs525 -n win2 "ssh cs525-05"; \
tmux split-window -h -t cs525:win2 "ssh cs525-06"; \
tmux split-window -v -t cs525:win2.0 "ssh cs525-07"; \
tmux split-window -v -t cs525:win2.1 "ssh cs525-08"; \
tmux select-layout -t cs525:win2 tiled; \
tmux new-window -t cs525 -n win3 "ssh cs525-09"; \
tmux split-window -h -t cs525:win3 "ssh cs525-10"; \
tmux split-window -v -t cs525:win3.0 "ssh cs525-11"; \
tmux split-window -v -t cs525:win3.1 "ssh cs525-12"; \
tmux select-layout -t cs525:win3 tiled; \
tmux new-window -t cs525 -n win4 "ssh cs525-13"; \
tmux split-window -h -t cs525:win4 "ssh cs525-14"; \
tmux split-window -v -t cs525:win4.0 "ssh cs525-15"; \
tmux split-window -v -t cs525:win4.1 "ssh cs525-16"; \
tmux select-layout -t cs525:win4 tiled; \
tmux new-window -t cs525 -n win5 "ssh cs525-17"; \
tmux split-window -h -t cs525:win5 "ssh cs525-18"; \
tmux split-window -v -t cs525:win5.0 "ssh cs525-19"; \
tmux split-window -v -t cs525:win5.1 "ssh cs525-20"; \
tmux select-layout -t cs525:win5 tiled; \