package vote.hackthe.georgia.ui.vote;

import android.app.Activity;
import android.content.Intent;
import android.os.Bundle;

import com.google.android.material.floatingactionbutton.FloatingActionButton;

import androidx.appcompat.app.AppCompatActivity;
import androidx.appcompat.widget.Toolbar;

import android.view.View;
import android.widget.RadioGroup;
import android.widget.Toast;

import vote.hackthe.georgia.R;
import vote.hackthe.georgia.NetworkUtils;

public class VoteActivity extends AppCompatActivity {

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_vote);
        Intent intent=getIntent();
        final String token = intent.getStringExtra("token");
        Toolbar toolbar = findViewById(R.id.toolbar);
        setSupportActionBar(toolbar);
        final RadioGroup group = findViewById(R.id.vote_selection);

        FloatingActionButton fab = findViewById(R.id.fab);
        fab.setOnClickListener(new View.OnClickListener() {
            @Override
            public void onClick(View view) {
                int id = group.getCheckedRadioButtonId();
                String vote = "";
                switch(id) {
                    case -1:
                        Toast.makeText(getApplicationContext(), getString(R.string.select_vote), Toast.LENGTH_LONG).show();
                        return;
                    case R.id.lincolnButton:
                        vote = "lincoln";
                        break;
                    case R.id.washingtonButton:
                        vote = "washington";
                        break;
                    case R.id.abstainButton:
                        vote = "abstain";
                        break;
                }
                final String finalVote = vote;
                new Thread(new Runnable() {
                    public void run() {
                        NetworkUtils.voteRequest(finalVote, token);
                    }
                }).start();
                Toast.makeText(getApplicationContext(), getString(R.string.voted), Toast.LENGTH_LONG).show();
                setResult(Activity.RESULT_OK);
                finish();
            }
        });
    }
}